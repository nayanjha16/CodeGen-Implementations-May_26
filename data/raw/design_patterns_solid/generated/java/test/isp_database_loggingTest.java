package org.example.patterns;
public class DatabaseIspTest {
    public static void main(String[] args) {
        DatabaseStore st = new DatabaseStore();
        st.write("x");
        if (!DatabaseIspClient.mirror(st).equals("database:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
