/// Data model representing a job posting input from the user.
class JobPosting {
  final String company;
  final String salary;
  final String description;
  final String applyLink;

  JobPosting({
    required this.company,
    required this.salary,
    required this.description,
    required this.applyLink,
  });

  Map<String, dynamic> toJson() {
    return {
      'company': company,
      'salary': salary,
      'description': description,
      'apply_link': applyLink,
    };
  }
}
