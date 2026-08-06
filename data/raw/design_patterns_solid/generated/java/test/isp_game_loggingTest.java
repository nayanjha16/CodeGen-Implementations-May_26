package org.example.patterns;
public class GameIspTest {
    public static void main(String[] args) {
        GameStore st = new GameStore();
        st.write("x");
        if (!GameIspClient.mirror(st).equals("game:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
