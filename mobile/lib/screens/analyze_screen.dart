import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import 'result_screen.dart';

/// Analyze screen — premium glass form.
class AnalyzeScreen extends StatefulWidget {
  final User? user;
  const AnalyzeScreen({super.key, this.user});

  @override
  State<AnalyzeScreen> createState() => _AnalyzeScreenState();
}

class _AnalyzeScreenState extends State<AnalyzeScreen> {
  final _companyCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _urlCtrl = TextEditingController();
  XFile? _image;
  bool _analyzing = false;

  Future<void> _pickImage() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (picked != null) setState(() => _image = picked);
  }

  Future<void> _analyze() async {
    final hasInput = _companyCtrl.text.isNotEmpty ||
        _descCtrl.text.isNotEmpty ||
        _urlCtrl.text.isNotEmpty ||
        _image != null;

    if (!hasInput) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please provide at least one input')),
      );
      return;
    }

    setState(() => _analyzing = true);

    try {
      final result = await ApiService.analyze(
        companyName: _companyCtrl.text,
        jobDescription: _descCtrl.text,
        url: _urlCtrl.text,
        image: _image,
      );

      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('Error: $e'),
              backgroundColor: const Color(0xFFEF4444)),
        );
      }
    } finally {
      if (mounted) setState(() => _analyzing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 8),
            const Text(
              'Analyze Job Posting',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w700,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Enter any combination of inputs for analysis.',
              style:
                  TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 13),
            ),
            const SizedBox(height: 28),

            // Company name
            _GlassField(
              controller: _companyCtrl,
              label: 'Company Name',
              icon: Icons.business_outlined,
            ),
            const SizedBox(height: 16),

            // URL
            _GlassField(
              controller: _urlCtrl,
              label: 'Job Posting URL',
              icon: Icons.link_outlined,
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 16),

            // Description
            _GlassField(
              controller: _descCtrl,
              label: 'Job Description',
              icon: Icons.description_outlined,
              maxLines: 5,
            ),
            const SizedBox(height: 16),

            // Image picker
            GestureDetector(
              onTap: _pickImage,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      color: Colors.white.withValues(alpha: 0.06),
                      border: Border.all(
                        color: _image != null
                            ? const Color(0xFF8B5CF6).withValues(alpha: 0.4)
                            : Colors.white.withValues(alpha: 0.12),
                      ),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          _image != null
                              ? Icons.check_circle_rounded
                              : Icons.image_outlined,
                          color: _image != null
                              ? const Color(0xFF8B5CF6)
                              : Colors.white.withValues(alpha: 0.2),
                          size: 32,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _image != null
                              ? 'Image selected: ${_image!.name}'
                              : 'Tap to upload screenshot (optional)',
                          style: TextStyle(
                            color: _image != null
                                ? Colors.white.withValues(alpha: 0.7)
                                : Colors.white.withValues(alpha: 0.3),
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 28),

            // Analyze button — gradient violet
            SizedBox(
              width: double.infinity,
              height: 56,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF8B5CF6), Color(0xFF6D28D9)],
                  ),
                  borderRadius: BorderRadius.circular(28),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF8B5CF6).withValues(alpha: 0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: ElevatedButton(
                  onPressed: _analyzing ? null : _analyze,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(28),
                    ),
                  ),
                  child: _analyzing
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text(
                          'Analyze',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Glass-morphism text field.
class _GlassField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final IconData icon;
  final int maxLines;
  final TextInputType? keyboardType;

  const _GlassField({
    required this.controller,
    required this.label,
    required this.icon,
    this.maxLines = 1,
    this.keyboardType,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
          ),
          child: TextField(
            controller: controller,
            maxLines: maxLines,
            keyboardType: keyboardType,
            style: const TextStyle(fontSize: 14),
            decoration: InputDecoration(
              labelText: label,
              labelStyle: TextStyle(
                  color: Colors.white.withValues(alpha: 0.35), fontSize: 13),
              prefixIcon: maxLines > 1
                  ? Padding(
                      padding: const EdgeInsets.only(bottom: 80),
                      child: Icon(icon,
                          size: 20, color: Colors.white.withValues(alpha: 0.25)),
                    )
                  : Icon(icon, size: 20, color: Colors.white.withValues(alpha: 0.25)),
              alignLabelWithHint: maxLines > 1,
              filled: false,
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
          ),
        ),
      ),
    );
  }
}
