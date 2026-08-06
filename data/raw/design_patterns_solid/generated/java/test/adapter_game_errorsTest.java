package org.example.patterns;
public class GameAdapterTest {
    public static void main(String[] args) {
        GameTarget t = new GameAdapter(new GameLegacyApi());
        if (!t.fetch().equals("modern-game")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
