// Student Gradebook Mini-Project
// A complete system demonstrating structs, Vec, HashMap, and methods
//
// TODO: Implement the missing pieces marked with "TODO"
// Run tests with: cargo test (after creating a proper cargo project)

use std::collections::HashMap;

// TODO 1: Implement the Student struct
// Fields: id (u32), name (String), grades (HashMap<String, f32>)
// The grades map stores course_name -> grade_percentage
//
// Hint: #[derive(Debug, Clone)] to start

// TODO 2: Implement methods for Student:
// - new(id: u32, name: &str) -> Self  (constructor)
// - add_grade(&mut self, course: &str, grade: f32)
// - get_average(&self) -> Option<f32>  (returns None if no grades)
// - get_letter_grade(&self) -> Option<char>  // A: 90+, B: 80+, C: 70+, D: 60+, F: <60


// TODO 3: Implement the Gradebook struct
// Fields: students (Vec<Student>)
//
// Methods to implement:
// - new() -> Self  (empty gradebook)
// - add_student(&mut self, student: Student)
// - find_student(&self, id: u32) -> Option<&Student>
// - find_student_mut(&mut self, id: u32) -> Option<&mut Student>
// - get_class_average(&self, course: &str) -> Option<f32>
// - get_top_student(&self) -> Option<&Student>  (by average grade)
// - get_failing_students(&self) -> Vec<&Student>  (any grade < 60)
// - print_report(&self)  (pretty print all students and their averages)


fn main() {
    println!("Student Gradebook System");
    println!("========================\n");
    
    // TODO 4: Create a gradebook and add at least 3 students
    // Example data:
    // - Alice (id: 1): Math=95, Science=88, History=92
    // - Bob (id: 2): Math=72, Science=65, History=58
    // - Carol (id: 3): Math=88, Science=91, History=85
    
    // TODO 5: Print a full report showing all students, their grades, and averages
    
    // TODO 6: Find and print the top student
    
    // TODO 7: Find and print all failing students (any grade < 60)
    
    // TODO 8: Calculate and print the class average for "Math"
    
    println!("\n=== Stretch Goals ===");
    // BONUS: Add a method to get_course_stats(&self, course: &str) -> (f32, f32, f32)
    // Returns (min, max, average) for a course
    
    // BONUS: Add a method get_honor_roll(&self) -> Vec<&Student>
    // Returns students with average >= 90
}


// ===== TESTS =====
// Run with: cargo test

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_student_creation() {
        // TODO: Uncomment and make this pass
        // let student = Student::new(1, "Alice");
        // assert_eq!(student.id, 1);
        // assert_eq!(student.name, "Alice");
        // assert!(student.grades.is_empty());
    }

    #[test]
    fn test_add_and_get_grade() {
        // TODO: Test adding grades and calculating average
        // let mut student = Student::new(1, "Bob");
        // student.add_grade("Math", 85.0);
        // student.add_grade("Science", 90.0);
        // assert_eq!(student.get_average(), Some(87.5));
    }

    #[test]
    fn test_letter_grades() {
        // TODO: Test letter grade conversion
        // A: 90+, B: 80+, C: 70+, D: 60+, F: <60
    }

    #[test]
    fn test_gradebook_find_student() {
        // TODO: Test finding students by ID
    }

    #[test]
    fn test_class_average() {
        // TODO: Test calculating class average for a course
    }

    #[test]
    fn test_top_student() {
        // TODO: Test finding the student with highest average
    }

    #[test]
    fn test_failing_students() {
        // TODO: Test finding students with any grade < 60
    }
}


// ===== HINTS =====
/*
HINT 1: Struct definition skeleton
#[derive(Debug, Clone)]
struct Student {
    id: u32,
    name: String,
    grades: HashMap<String, f32>,
}

HINT 2: Average calculation
- Get all values from HashMap: self.grades.values()
- Sum them and divide by count
- Handle empty case with match or if

HINT 3: Entry API for HashMap
*counts.entry(key).or_insert(0) += 1;  // Get mutable reference

HINT 4: Iterator methods you'll need
.iter()           // Iterate over collection
.map(|x| ...)     // Transform each element
.filter(|x| ...)  // Keep only matching elements
.collect()        // Gather into Vec or other collection
.sum()             // Add all elements
.max()             // Find maximum (returns Option)
.min()             // Find minimum (returns Option)

HINT 5: Comparing students by average
students.iter()
    .max_by(|a, b| {
        a.get_average().unwrap_or(0.0)
            .partial_cmp(&b.get_average().unwrap_or(0.0))
            .unwrap()
    })

HINT 6: Using Option<f32>
Some(value) means we have a value
None means no value (e.g., no grades yet)
Use .unwrap_or(default) to extract or provide fallback
*/
