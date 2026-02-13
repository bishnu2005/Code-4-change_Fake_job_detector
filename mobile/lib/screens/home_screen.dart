import 'dart:ui';
import 'package:flutter/material.dart';
import '../models/feed_post.dart';
import '../models/user.dart';
import '../services/api_service.dart';

/// Reddit-style community feed with glass morphism.
class HomeScreen extends StatefulWidget {
  final User? user;
  const HomeScreen({super.key, this.user});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<FeedPost> _posts = [];
  bool _loading = true;
  String _filter = 'all';
  final TextEditingController _searchCtrl = TextEditingController();
  int? _nextCursor;

  @override
  void initState() {
    super.initState();
    _loadFeed();
  }

  Future<void> _loadFeed({bool append = false}) async {
    if (!append) setState(() => _loading = true);
    try {
      final data = await ApiService.getFeed(
        cursor: append ? _nextCursor : null,
        filter: _filter,
        search: _searchCtrl.text,
      );
      setState(() {
        if (append) {
          _posts.addAll(data['posts'] as List<FeedPost>);
        } else {
          _posts = data['posts'] as List<FeedPost>;
        }
        _nextCursor = data['next_cursor'] as int?;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _vote(int reportId, String type) async {
    if (widget.user == null) return;
    try {
      final result = await ApiService.vote(
        reportId: reportId,
        userId: widget.user!.id,
        voteType: type,
      );
      setState(() {
        final idx = _posts.indexWhere((p) => p.id == reportId);
        if (idx >= 0) {
          final old = _posts[idx];
          _posts[idx] = FeedPost(
            id: old.id,
            companyName: old.companyName,
            domain: old.domain,
            title: old.title,
            description: old.description,
            verdict: old.verdict,
            upvotes: result['upvotes'] as int,
            downvotes: result['downvotes'] as int,
            createdAt: old.createdAt,
            author: old.author,
          );
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: Colors.orange),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        children: [
          // Header with logo
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    'assets/images/logo.png',
                    height: 34,
                    width: 34,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(width: 10),
                const Text(
                  'HireLiar',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                    letterSpacing: -0.5,
                  ),
                ),
                const Spacer(),
                _GlassIconButton(
                  icon: Icons.add_rounded,
                  onTap: _showCreateDialog,
                ),
              ],
            ),
          ),

          // Glass search bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.06),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
                  ),
                  child: TextField(
                    controller: _searchCtrl,
                    style: const TextStyle(fontSize: 14),
                    decoration: InputDecoration(
                      hintText: 'Search company or domain...',
                      hintStyle:
                          TextStyle(color: Colors.white.withValues(alpha: 0.3)),
                      prefixIcon: Icon(Icons.search,
                          size: 20, color: Colors.white.withValues(alpha: 0.3)),
                      suffixIcon: _searchCtrl.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear, size: 16),
                              onPressed: () {
                                _searchCtrl.clear();
                                _loadFeed();
                              },
                            )
                          : null,
                      contentPadding: const EdgeInsets.symmetric(vertical: 12),
                      isDense: true,
                      filled: false,
                      border: InputBorder.none,
                      enabledBorder: InputBorder.none,
                      focusedBorder: InputBorder.none,
                    ),
                    onSubmitted: (_) => _loadFeed(),
                  ),
                ),
              ),
            ),
          ),

          // Filter chips
          SizedBox(
            height: 44,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                for (final f in ['all', 'scam', 'legit', 'credible', 'newest'])
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: ChoiceChip(
                      label: Text(
                        f == 'credible'
                            ? 'Most Credible'
                            : f[0].toUpperCase() + f.substring(1),
                      ),
                      selected: _filter == f,
                      selectedColor: const Color(0xFF8B5CF6).withValues(alpha: 0.2),
                      backgroundColor: Colors.white.withValues(alpha: 0.06),
                      side: BorderSide(
                        color: _filter == f
                            ? const Color(0xFF8B5CF6).withValues(alpha: 0.4)
                            : Colors.white.withValues(alpha: 0.08),
                      ),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20)),
                      labelStyle: TextStyle(
                        color: _filter == f
                            ? const Color(0xFF8B5CF6)
                            : Colors.white54,
                        fontSize: 12,
                        fontWeight:
                            _filter == f ? FontWeight.w600 : FontWeight.normal,
                      ),
                      onSelected: (_) {
                        setState(() => _filter = f);
                        _loadFeed();
                      },
                    ),
                  ),
              ],
            ),
          ),

          // Feed
          Expanded(
            child: _loading
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF8B5CF6)))
                : _posts.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.inbox_outlined,
                                size: 48,
                                color: Colors.white.withValues(alpha: 0.15)),
                            const SizedBox(height: 12),
                            Text('No reports yet',
                                style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.3),
                                    fontSize: 15)),
                            const SizedBox(height: 4),
                            Text('Be the first to contribute!',
                                style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.2),
                                    fontSize: 13)),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        color: const Color(0xFF8B5CF6),
                        onRefresh: () => _loadFeed(),
                        child: ListView.builder(
                          padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                          itemCount:
                              _posts.length + (_nextCursor != null ? 1 : 0),
                          itemBuilder: (ctx, i) {
                            if (i == _posts.length) {
                              _loadFeed(append: true);
                              return const Padding(
                                padding: EdgeInsets.all(16),
                                child:
                                    Center(child: CircularProgressIndicator()),
                              );
                            }
                            return _GlassFeedCard(
                              post: _posts[i],
                              onUpvote: () => _vote(_posts[i].id, 'up'),
                              onDownvote: () => _vote(_posts[i].id, 'down'),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  void _showCreateDialog() {
    if (widget.user == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please log in first')),
      );
      return;
    }

    final companyCtrl = TextEditingController();
    final domainCtrl = TextEditingController();
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    String verdict = 'suspicious';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => ClipRRect(
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 30, sigmaY: 30),
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFF151523).withValues(alpha: 0.95),
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(24)),
                border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
              ),
              padding: EdgeInsets.fromLTRB(
                20,
                20,
                20,
                MediaQuery.of(ctx).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Handle bar
                    Center(
                      child: Container(
                        width: 40,
                        height: 4,
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('New Report',
                        style: TextStyle(
                            fontSize: 20, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    TextField(
                      controller: companyCtrl,
                      decoration:
                          const InputDecoration(labelText: 'Company Name *'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: domainCtrl,
                      decoration:
                          const InputDecoration(labelText: 'Domain (optional)'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: titleCtrl,
                      decoration: const InputDecoration(labelText: 'Title *'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: descCtrl,
                      maxLines: 3,
                      decoration:
                          const InputDecoration(labelText: 'Description *'),
                    ),
                    const SizedBox(height: 14),
                    Wrap(
                      spacing: 8,
                      children: [
                        for (final v in ['scam', 'suspicious', 'legit'])
                          ChoiceChip(
                            label: Text(v[0].toUpperCase() + v.substring(1)),
                            selected: verdict == v,
                            selectedColor: v == 'scam'
                                ? const Color(0xFFEF4444).withValues(alpha: 0.2)
                                : v == 'legit'
                                    ? const Color(0xFF22C55E).withValues(alpha: 0.2)
                                    : const Color(0xFF8B5CF6).withValues(alpha: 0.2),
                            side: BorderSide(
                              color: v == 'scam' && verdict == v
                                  ? const Color(0xFFEF4444).withValues(alpha: 0.4)
                                  : v == 'legit' && verdict == v
                                      ? const Color(0xFF22C55E).withValues(alpha: 0.4)
                                      : v == 'suspicious' && verdict == v
                                          ? const Color(0xFF8B5CF6)
                                              .withValues(alpha: 0.4)
                                          : Colors.white.withValues(alpha: 0.08),
                            ),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20)),
                            labelStyle: TextStyle(
                              fontSize: 13,
                              color:
                                  verdict == v ? Colors.white : Colors.white54,
                            ),
                            onSelected: (_) => setSheetState(() => verdict = v),
                          ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF8B5CF6), Color(0xFF6D28D9)],
                          ),
                          borderRadius: BorderRadius.circular(26),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF8B5CF6).withValues(alpha: 0.3),
                              blurRadius: 16,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.transparent,
                            shadowColor: Colors.transparent,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(26),
                            ),
                          ),
                          onPressed: () async {
                            if (companyCtrl.text.isEmpty ||
                                titleCtrl.text.isEmpty ||
                                descCtrl.text.isEmpty) {
                              return;
                            }
                            await ApiService.createReport(
                              userId: widget.user!.id,
                              companyName: companyCtrl.text,
                              domain: domainCtrl.text.isNotEmpty
                                  ? domainCtrl.text
                                  : null,
                              title: titleCtrl.text,
                              description: descCtrl.text,
                              verdict: verdict,
                            );
                            if (context.mounted) Navigator.pop(ctx);
                            _loadFeed();
                          },
                          child: const Text('Submit Report',
                              style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ── Glass icon button ──────────────────────────────────────────

class _GlassIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _GlassIconButton({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.06),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
        ),
        child: Icon(icon, color: const Color(0xFF8B5CF6), size: 20),
      ),
    );
  }
}

// ── Glass feed card ────────────────────────────────────────────

class _GlassFeedCard extends StatelessWidget {
  final FeedPost post;
  final VoidCallback onUpvote;
  final VoidCallback onDownvote;

  const _GlassFeedCard({
    required this.post,
    required this.onUpvote,
    required this.onDownvote,
  });

  Color get _verdictColor {
    switch (post.verdict) {
      case 'scam':
        return const Color(0xFFEF4444);
      case 'legit':
        return const Color(0xFF22C55E);
      default:
        return const Color(0xFF8B5CF6);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.35),
            blurRadius: 32,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header row
                Row(
                  children: [
                    CircleAvatar(
                      radius: 16,
                      backgroundColor:
                          const Color(0xFF8B5CF6).withValues(alpha: 0.15),
                      child: Text(
                        post.author.username[0].toUpperCase(),
                        style: const TextStyle(
                          color: Color(0xFF8B5CF6),
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            post.author.username,
                            style: const TextStyle(
                                fontWeight: FontWeight.w600, fontSize: 13),
                          ),
                          Text(
                            post.timeAgo,
                            style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.3),
                                fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                    // Verdict pill
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 5),
                      decoration: BoxDecoration(
                        color: _verdictColor.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(20),
                        border:
                            Border.all(color: _verdictColor.withValues(alpha: 0.3)),
                      ),
                      child: Text(
                        post.verdict.toUpperCase(),
                        style: TextStyle(
                          color: _verdictColor,
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Company name
                Text(
                  post.companyName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.3,
                  ),
                ),

                // Domain glass chip
                if (post.domain != null && post.domain!.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 6),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.06),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                    ),
                    child: Text(
                      post.domain!,
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.5),
                        fontSize: 11,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ),

                const SizedBox(height: 10),
                Text(
                  post.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w500, fontSize: 14),
                ),
                const SizedBox(height: 4),
                Text(
                  post.description,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.5),
                      fontSize: 13,
                      height: 1.4),
                ),
                const SizedBox(height: 14),

                // Vote row
                Row(
                  children: [
                    _VoteChip(
                      icon: Icons.arrow_upward_rounded,
                      count: post.upvotes,
                      color: const Color(0xFF22C55E),
                      onTap: onUpvote,
                    ),
                    const SizedBox(width: 10),
                    _VoteChip(
                      icon: Icons.arrow_downward_rounded,
                      count: post.downvotes,
                      color: const Color(0xFFEF4444),
                      onTap: onDownvote,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _VoteChip extends StatelessWidget {
  final IconData icon;
  final int count;
  final Color color;
  final VoidCallback onTap;

  const _VoteChip({
    required this.icon,
    required this.count,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.15)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 15, color: color.withValues(alpha: 0.8)),
            const SizedBox(width: 5),
            Text('$count',
                style: TextStyle(color: color.withValues(alpha: 0.8), fontSize: 13)),
          ],
        ),
      ),
    );
  }
}
