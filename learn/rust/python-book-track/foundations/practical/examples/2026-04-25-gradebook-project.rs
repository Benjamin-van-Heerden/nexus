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
#[derive(Debug, Clone)]
struct Student {
    _id: u32,
    name: String,
    grades: HashMap<String, f32>,
}

// TODO 2: Implement methods for Student:
// - new(id: u32, name: &str) -> Self  (constructor)
// - add_grade(&mut self, course: &str, grade: f32)
// - get_average(&self) -> Option<f32>  (returns None if no grades)
// - get_letter_grade(&self) -> Option<char>  // A: 90+, B: 80+, C: 70+, D: 60+, F: <60

impl Student {
    fn new(id: u32, name: &str) -> Self {
        Self {
            _id: id,
            name: name.to_string(),
            grades: HashMap::new(),
        }
    }

    fn add_grade(&mut self, course: &str, grade: f32) {
        self.grades.insert(course.to_string(), grade);
    }

    fn get_average(&self) -> Option<f32> {
        if self.grades.is_empty() {
            None
        } else {
            let sum: f32 = self.grades.values().sum();
            Some(sum / self.grades.len() as f32)
        }
    }

    fn get_letter_grade(&self) -> Option<char> {
        match self.get_average() {
            None => None,
            Some(avg) => {
                let letter = match avg {
                    avg if avg >= 90.0 => 'A',
                    avg if avg >= 80.0 => 'B',
                    avg if avg >= 70.0 => 'C',
                    avg if avg >= 60.0 => 'D',
                    _ => 'F',
                };
                Some(letter)
            }
        }
    }
}

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

#[derive(Debug, Clone)]
struct Gradebook {
    students: Vec<Student>,
}

impl Gradebook {
    fn new() -> Self {
        Self { students: vec![] }
    }

    fn add_student(&mut self, student: Student) {
        self.students.push(student);
    }

    fn _find_student(&self, id: u32) -> Option<&Student> {
        self.students.iter().find(|s| s._id == id)
    }

    fn _find_student_mut(&mut self, id: u32) -> Option<&mut Student> {
        self.students.iter_mut().find(|s| s._id == id)
    }

    fn get_class_average(&self, course: &str) -> Option<f32> {
        let grades = self
            .students
            .iter()
            .map(|s| s.grades.get(course))
            .collect::<Option<Vec<&f32>>>()?;
        if grades.len() == 0 {
            None
        } else {
            let len = grades.len() as f32;
            Some(grades.into_iter().sum::<f32>() / len)
        }
    }

    fn get_top_student(&self) -> Option<&Student> {
        self.students.iter().max_by(|a, b| {
            a.get_average()
                .unwrap_or(0.0)
                .total_cmp(&b.get_average().unwrap_or(0.0))
        })
    }
    fn get_failing_students(&self) -> Vec<&Student> {
        self.students
            .iter()
            .filter(|s| s.get_average().unwrap_or(0.0) < 60.0)
            .collect()
    }

    fn print_report(&self) {
        self.students.iter().map(|s| println!("{:?}", s)).collect()
    }

    fn get_course_stats(&self, course: &str) -> Option<(f32, f32, f32)> {
        let grades: Vec<f32> = self
            .students
            .iter()
            .filter_map(|s| s.grades.get(course).copied())
            .collect();

        if grades.is_empty() {
            return None;
        }

        let min = grades.iter().copied().min_by(f32::total_cmp).unwrap();
        let max = grades.iter().copied().max_by(f32::total_cmp).unwrap();
        let avg = grades.iter().sum::<f32>() / grades.len() as f32;

        Some((min, max, avg))
    }

    fn get_honor_roll(&self) -> Vec<&Student> {
        self.students
            .iter()
            .filter(|s| s.get_average().is_some_and(|avg| avg >= 90.0))
            .collect()
    }
}

fn main() {
    println!("Student Gradebook System");
    println!("========================\n");

    // TODO 4: Create a gradebook and add at least 3 students
    // Example data:
    // - Alice (id: 1): Math=95, Science=88, History=92
    // - Bob (id: 2): Math=72, Science=65, History=58
    // - Carol (id: 3): Math=88, Science=91, History=85
    let mut gradebook = Gradebook::new();

    let mut alice = Student::new(3, "Alice");
    alice.add_grade("Math", 95.0);
    alice.add_grade("Science", 88.0);
    alice.add_grade("History", 92.0);

    let mut bob = Student::new(3, "Bob");
    bob.add_grade("Math", 60.0);
    bob.add_grade("Science", 50.0);
    bob.add_grade("History", 58.0);

    let mut carol = Student::new(3, "Carol");
    carol.add_grade("Math", 88.0);
    carol.add_grade("Science", 88.0);
    carol.add_grade("History", 88.0);

    gradebook.add_student(alice);
    gradebook.add_student(bob);
    gradebook.add_student(carol);

    // TODO 5: Print a full report showing all students, their grades, and averages
    gradebook.print_report();

    // TODO 6: Find and print the top student
    println!();
    let top_student = gradebook.get_top_student();
    println!("The top student is {:?}", top_student.unwrap());

    // TODO 7: Find and print all failing students (any grade < 60)
    println!();
    let failing_students = gradebook.get_failing_students();
    println!(
        "Failing students: {:?}",
        failing_students
            .iter()
            .map(|s| s.name.clone())
            .collect::<String>()
    );

    // TODO 8: Calculate and print the class average for "Math"
    println!();
    let math_average = gradebook.get_class_average("Math");
    println!("The class average for Math is: {}", math_average.unwrap());

    println!("\n=== Stretch Goals ===");

    if let Some((min, max, avg)) = gradebook.get_course_stats("Math") {
        println!("Math stats — min: {min}, max: {max}, avg: {avg}");
    }

    let honor_roll = gradebook.get_honor_roll();
    println!(
        "Honor roll: {}",
        honor_roll
            .iter()
            .map(|s| s.name.clone())
            .collect::<Vec<_>>()
            .join(", ")
    );
}

// ===== TESTS =====
// Run with: cargo test

#[cfg(test)]
mod tests {
    use super::*;

    fn student_with(id: u32, name: &str, grades: &[(&str, f32)]) -> Student {
        let mut s = Student::new(id, name);
        for (course, grade) in grades {
            s.add_grade(course, *grade);
        }
        s
    }

    #[test]
    fn test_student_creation() {
        let student = Student::new(1, "Alice");
        assert_eq!(student._id, 1);
        assert_eq!(student.name, "Alice");
        assert!(student.grades.is_empty());
        assert_eq!(student.get_average(), None);
        assert_eq!(student.get_letter_grade(), None);
    }

    #[test]
    fn test_add_and_get_grade() {
        let mut student = Student::new(1, "Bob");
        student.add_grade("Math", 85.0);
        student.add_grade("Science", 90.0);
        assert_eq!(student.get_average(), Some(87.5));

        student.add_grade("Math", 100.0);
        assert_eq!(student.grades.len(), 2);
        assert_eq!(student.grades.get("Math"), Some(&100.0));
    }

    #[test]
    fn test_letter_grades() {
        let cases = [
            (95.0, 'A'),
            (90.0, 'A'),
            (89.99, 'B'),
            (80.0, 'B'),
            (75.0, 'C'),
            (70.0, 'C'),
            (65.0, 'D'),
            (60.0, 'D'),
            (59.99, 'F'),
            (0.0, 'F'),
        ];
        for (grade, expected) in cases {
            let s = student_with(1, "T", &[("X", grade)]);
            assert_eq!(s.get_letter_grade(), Some(expected), "grade {grade}");
        }

        assert_eq!(Student::new(1, "Empty").get_letter_grade(), None);
    }

    #[test]
    fn test_gradebook_find_student() {
        let mut gb = Gradebook::new();
        gb.add_student(Student::new(1, "Alice"));
        gb.add_student(Student::new(2, "Bob"));

        assert_eq!(gb._find_student(1).unwrap().name, "Alice");
        assert_eq!(gb._find_student(2).unwrap().name, "Bob");
        assert!(gb._find_student(99).is_none());

        gb._find_student_mut(1).unwrap().add_grade("Math", 100.0);
        assert_eq!(
            gb._find_student(1).unwrap().grades.get("Math"),
            Some(&100.0)
        );
        assert!(gb._find_student_mut(99).is_none());
    }

    #[test]
    fn test_class_average() {
        let mut gb = Gradebook::new();
        assert_eq!(gb.get_class_average("Math"), None);

        gb.add_student(student_with(1, "A", &[("Math", 80.0)]));
        gb.add_student(student_with(2, "B", &[("Math", 100.0)]));
        assert_eq!(gb.get_class_average("Math"), Some(90.0));

        // current impl short-circuits to None when any student is missing the course
        gb.add_student(student_with(3, "C", &[("Science", 70.0)]));
        assert_eq!(gb.get_class_average("Math"), None);
    }

    #[test]
    fn test_top_student() {
        let mut gb = Gradebook::new();
        assert!(gb.get_top_student().is_none());

        gb.add_student(student_with(1, "A", &[("Math", 70.0)]));
        gb.add_student(student_with(2, "B", &[("Math", 90.0)]));
        gb.add_student(student_with(3, "C", &[("Math", 80.0)]));

        assert_eq!(gb.get_top_student().unwrap().name, "B");
    }

    #[test]
    fn test_failing_students() {
        let mut gb = Gradebook::new();
        gb.add_student(student_with(1, "Pass", &[("Math", 85.0), ("Sci", 90.0)]));
        gb.add_student(student_with(2, "FailAvg", &[("Math", 50.0), ("Sci", 55.0)]));
        gb.add_student(student_with(3, "Borderline", &[("Math", 60.0)]));

        let failing = gb.get_failing_students();
        let names: Vec<&str> = failing.iter().map(|s| s.name.as_str()).collect();
        assert_eq!(names, vec!["FailAvg"]);
    }

    #[test]
    fn test_course_stats() {
        let mut gb = Gradebook::new();
        assert_eq!(gb.get_course_stats("Math"), None);

        gb.add_student(student_with(1, "A", &[("Math", 60.0)]));
        gb.add_student(student_with(2, "B", &[("Math", 100.0)]));
        gb.add_student(student_with(3, "C", &[("Math", 80.0)]));
        gb.add_student(student_with(4, "D", &[("Science", 95.0)])); // no Math

        let (min, max, avg) = gb.get_course_stats("Math").unwrap();
        assert_eq!(min, 60.0);
        assert_eq!(max, 100.0);
        assert_eq!(avg, 80.0);
    }

    #[test]
    fn test_honor_roll() {
        let mut gb = Gradebook::new();
        gb.add_student(student_with(1, "A", &[("X", 95.0)]));
        gb.add_student(student_with(2, "B", &[("X", 89.99)]));
        gb.add_student(student_with(3, "C", &[("X", 90.0)]));
        gb.add_student(Student::new(4, "Empty"));

        let names: Vec<&str> = gb
            .get_honor_roll()
            .iter()
            .map(|s| s.name.as_str())
            .collect();
        assert_eq!(names, vec!["A", "C"]);
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
