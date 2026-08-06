package org.example.patterns;
public class ReportIteratorTest {
    public static void main(String[] args) {
        ReportCollection col = new ReportCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("report:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
