import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/job_posting.dart';
import '../models/prediction_result.dart';
import '../services/api_service.dart';
import '../widgets/input_form.dart';
import '../widgets/loading_overlay.dart';
import 'result_screen.dart';

/// Home screen with unified multi-signal input form.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _companyController = TextEditingController();
  final _salaryController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _applyLinkController = TextEditingController();
  bool _isLoading = false;
  File? _selectedImage;
  String? _selectedImageName;

  @override
  void dispose() {
    _companyController.dispose();
    _salaryController.dispose();
    _descriptionController.dispose();
    _applyLinkController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked != null) {
      setState(() {
        _selectedImage = File(picked.path);
        _selectedImageName = picked.name;
      });
    }
  }

  void _removeImage() {
    setState(() {
      _selectedImage = null;
      _selectedImageName = null;
    });
  }

  Future<void> _analyzePosting() async {
    // Allow submission if description OR image is provided
    final hasDescription = _descriptionController.text.trim().isNotEmpty;
    final hasImage = _selectedImage != null;

    if (!hasDescription && !hasImage) {
      _showInsufficientDataDialog();
      return;
    }

    // Validate form only if user typed something
    if (hasDescription && !_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final posting = JobPosting(
        company: _companyController.text.trim(),
        salary: _salaryController.text.trim(),
        description: _descriptionController.text.trim(),
        applyLink: _applyLinkController.text.trim(),
      );

      final result = await ApiService.analyze(
        posting,
        imageFile: _selectedImage,
      );

      // Handle sufficiency_level = "None" from backend
      if (result.sufficiencyLevel == 'None') {
        if (mounted) {
          _showInsufficientDataDialog();
        }
        return;
      }

      _navigateToResult(result);
    } on ApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('An unexpected error occurred: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _navigateToResult(PredictionResult result) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ResultScreen(result: result),
      ),
    );
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.redAccent,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  void _showInsufficientDataDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E1B3A),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(Icons.warning_amber_rounded,
                color: Colors.amber.shade400, size: 28),
            const SizedBox(width: 10),
            const Text('Insufficient Data',
                style: TextStyle(color: Colors.white, fontSize: 18)),
          ],
        ),
        content: const Text(
          'Please provide at least a job description, a URL, or an image to analyze.',
          style: TextStyle(color: Colors.white70, fontSize: 14, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK',
                style: TextStyle(color: Colors.tealAccent, fontSize: 15)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: LoadingOverlay(
        isLoading: _isLoading,
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color(0xFF0F0C29),
                Color(0xFF302B63),
                Color(0xFF24243E),
              ],
            ),
          ),
          child: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Header
                  const Icon(Icons.shield_rounded,
                      color: Colors.tealAccent, size: 48),
                  const SizedBox(height: 12),
                  const Text(
                    'Fake Job Detector',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Multi-signal fraud intelligence system',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.5),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Form
                  InputForm(
                    formKey: _formKey,
                    companyController: _companyController,
                    salaryController: _salaryController,
                    descriptionController: _descriptionController,
                    applyLinkController: _applyLinkController,
                  ),
                  const SizedBox(height: 20),

                  // ── Image Upload (Optional Signal) ──────────
                  _buildImageSection(),
                  const SizedBox(height: 28),

                  // ── Analyze Button ──────────────────────────
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _analyzePosting,
                    icon: const Icon(Icons.search_rounded),
                    label: const Text('Analyze Job Posting',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w600)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.tealAccent,
                      foregroundColor: const Color(0xFF0F0C29),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14)),
                      elevation: 4,
                    ),
                  ),
                  const SizedBox(height: 10),

                  // Subtle caption
                  Text(
                    'The more details you provide, the more accurate the assessment.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.35),
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImageSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.08),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Image upload button or selection indicator
          if (_selectedImage == null) ...[
            OutlinedButton.icon(
              onPressed: _isLoading ? null : _pickImage,
              icon: const Icon(Icons.add_photo_alternate_rounded, size: 20),
              label: const Text('Attach Image (Optional)',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.tealAccent.withValues(alpha: 0.8),
                side: BorderSide(
                    color: Colors.tealAccent.withValues(alpha: 0.3), width: 1),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ] else ...[
            // Selected image indicator
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.tealAccent.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: Colors.tealAccent.withValues(alpha: 0.25)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.image_rounded,
                      color: Colors.tealAccent, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _selectedImageName ?? 'Image selected',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.8),
                        fontSize: 13,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  InkWell(
                    onTap: _removeImage,
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: Colors.redAccent.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.close_rounded,
                          color: Colors.redAccent, size: 16),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 8),
          // Helper text
          Text(
            'Optional: Add screenshot of job posting for stronger fraud analysis.',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.3),
              fontSize: 11,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }
}
