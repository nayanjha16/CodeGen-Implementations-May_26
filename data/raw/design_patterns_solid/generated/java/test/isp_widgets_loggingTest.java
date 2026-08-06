package org.example.patterns;
public class WidgetsIspTest {
    public static void main(String[] args) {
        WidgetsStore st = new WidgetsStore();
        st.write("x");
        if (!WidgetsIspClient.mirror(st).equals("widgets:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
