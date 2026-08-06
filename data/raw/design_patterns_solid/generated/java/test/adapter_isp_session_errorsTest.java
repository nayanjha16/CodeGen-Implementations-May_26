package org.example.patterns;
public class SessionAdapterTest {
    public static void main(String[] args) {
        SessionTarget t = new SessionAdapter(new SessionLegacyApi());
        if (!t.fetch().equals("modern-session")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
