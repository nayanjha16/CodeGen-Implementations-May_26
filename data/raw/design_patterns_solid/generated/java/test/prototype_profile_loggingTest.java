package org.example.patterns;
public class ProfilePrototypeTest {
    public static void main(String[] args) {
        ProfilePrototype a = new ProfilePrototype("profile", 2);
        ProfilePrototype b = a.copy();
        b.setLabel("profile-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
