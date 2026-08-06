package org.example.patterns;
public class EmailIteratorTest {
    public static void main(String[] args) {
        EmailCollection col = new EmailCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("email:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
