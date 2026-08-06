package org.example.patterns;
public class AuthAdapterTest {
    public static void main(String[] args) {
        AuthTarget t = new AuthAdapter(new AuthLegacyApi());
        if (!t.fetch().equals("modern-auth")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
