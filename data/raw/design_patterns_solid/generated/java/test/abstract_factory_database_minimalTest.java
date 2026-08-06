package org.example.patterns;
public class DatabaseAbstractFactoryTest {
    public static void main(String[] args) {
        String out = DatabaseAbstractFactoryDemo.run(new DatabaseCloudFactory());
        if (!out.equals("cloud-btn-database|cloud-dlg-database")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
