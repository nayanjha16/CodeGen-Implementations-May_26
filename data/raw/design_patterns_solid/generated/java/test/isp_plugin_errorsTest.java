package org.example.patterns;
public class PluginIspTest {
    public static void main(String[] args) {
        PluginStore st = new PluginStore();
        st.write("x");
        if (!PluginIspClient.mirror(st).equals("plugin:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
