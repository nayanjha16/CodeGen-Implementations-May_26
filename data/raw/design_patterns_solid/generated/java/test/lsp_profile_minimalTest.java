package org.example.patterns;
public class ProfileLspTest {
    public static void main(String[] args) {
        ProfileShape[] arr = new ProfileShape[] { new ProfileRectangle(2,3), new ProfileSquare(4) };
        if (ProfileLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
