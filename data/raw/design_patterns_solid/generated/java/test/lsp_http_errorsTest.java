package org.example.patterns;
public class HttpLspTest {
    public static void main(String[] args) {
        HttpShape[] arr = new HttpShape[] { new HttpRectangle(2,3), new HttpSquare(4) };
        if (HttpLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
