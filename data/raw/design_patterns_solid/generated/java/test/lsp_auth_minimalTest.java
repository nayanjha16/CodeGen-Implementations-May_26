package org.example.patterns;
public class AuthLspTest {
    public static void main(String[] args) {
        AuthShape[] arr = new AuthShape[] { new AuthRectangle(2,3), new AuthSquare(4) };
        if (AuthLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
