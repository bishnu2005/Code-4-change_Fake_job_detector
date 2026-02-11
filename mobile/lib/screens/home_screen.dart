import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/job_posting.dart';
import '../models/prediction_result.dart';
import '../services/api_service.dart';
import '../widgets/input_form.dart';
import '../widgets/loading_overlay.dart';
import 'result_screen.dart';

/// Home screen with job posting input form and image upload.
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

  @override
  void dispose() {
    _companyController.dispose();
    _salaryController.dispose();
    _descriptionController.dispose();
    _applyLinkController.dispose();
    super.dispose();
  }

  Future<void> _analyzeText() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final posting = JobPosting(
        company: _companyController.text.trim(),
        salary: _salaryController.text.trim(),
        description: _descriptionController.text.trim(),
        applyLink: _applyLinkController.text.trim(),
      );

      final result = await ApiService.analyzeText(posting);
      _navigateToResult(result);
    } on ApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('An unexpected error occurred: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _analyzeImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;

    setState(() => _isLoading = true);

    try {
      final result = await ApiService.analyzeImage(File(picked.path));
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
                    'Paste a job posting to analyze for fraud signals',
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
                  const SizedBox(height: 28),

                  // Analyze Text button
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _analyzeText,
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
                  const SizedBox(height: 16),

                  // Divider
                  Row(
                    children: [
                      Expanded(
                          child: Divider(
                              color: Colors.white.withValues(alpha: 0.15))),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Text('OR',
                            style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.4),
                                fontSize: 13)),
                      ),
                      Expanded(
                          child: Divider(
                              color: Colors.white.withValues(alpha: 0.15))),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Upload Image button
                  OutlinedButton.icon(
                    onPressed: _isLoading ? null : _analyzeImage,
                    icon: const Icon(Icons.image_rounded),
                    label: const Text('Upload Image (OCR)',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w600)),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.tealAccent,
                      side: const BorderSide(
                          color: Colors.tealAccent, width: 1.5),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14)),
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
}
