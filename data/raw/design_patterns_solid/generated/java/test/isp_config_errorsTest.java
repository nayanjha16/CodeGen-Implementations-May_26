package org.example.patterns;
public class ConfigIspTest {
    public static void main(String[] args) {
        ConfigStore st = new ConfigStore();
        st.write("x");
        if (!ConfigIspClient.mirror(st).equals("config:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
