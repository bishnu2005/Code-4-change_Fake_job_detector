import 'package:flutter/material.dart';

/// Reusable input form widget for job posting fields.
class InputForm extends StatefulWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController companyController;
  final TextEditingController salaryController;
  final TextEditingController descriptionController;
  final TextEditingController applyLinkController;

  const InputForm({
    super.key,
    required this.formKey,
    required this.companyController,
    required this.salaryController,
    required this.descriptionController,
    required this.applyLinkController,
  });

  @override
  State<InputForm> createState() => _InputFormState();
}

class _InputFormState extends State<InputForm> {
  @override
  Widget build(BuildContext context) {
    return Form(
      key: widget.formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildField(
            controller: widget.companyController,
            label: 'Company Name',
            icon: Icons.business,
            hint: 'e.g., Google, Microsoft',
          ),
          const SizedBox(height: 16),
          _buildField(
            controller: widget.salaryController,
            label: 'Salary',
            icon: Icons.attach_money,
            hint: 'e.g., ₹80,000 - ₹120,000/year',
          ),
          const SizedBox(height: 16),
          _buildField(
            controller: widget.descriptionController,
            label: 'Job Description',
            icon: Icons.description,
            hint: 'Paste the full job posting text here...',
            maxLines: 6,
          ),
          const SizedBox(height: 16),
          _buildField(
            controller: widget.applyLinkController,
            label: 'Apply Link / URL',
            icon: Icons.link,
            hint: 'e.g., https://careers.example.com/apply',
          ),
        ],
      ),
    );
  }

  Widget _buildField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    required String hint,
    int maxLines = 1,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      maxLines: maxLines,
      validator: validator,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3)),
        labelStyle: TextStyle(color: Colors.white.withValues(alpha: 0.7)),
        prefixIcon: Icon(icon, color: Colors.tealAccent),
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.08),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.tealAccent, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.redAccent, width: 1.5),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
    );
  }
}
