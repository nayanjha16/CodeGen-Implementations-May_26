package org.example.patterns;
public class ProfileSingletonTest {
    public static void main(String[] args) {
        ProfileSingleton a = ProfileSingleton.getInstance();
        ProfileSingleton b = ProfileSingleton.getInstance();
        a.setValue("profile-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("profile-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
