package org.example.patterns;
public class PaymentsLspTest {
    public static void main(String[] args) {
        PaymentsShape[] arr = new PaymentsShape[] { new PaymentsRectangle(2,3), new PaymentsSquare(4) };
        if (PaymentsLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
