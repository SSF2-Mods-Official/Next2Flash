// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_hurt_103

package fox_fla
{
    import flash.display.MovieClip;
    import flash.display.*;
    import flash.geom.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class fox_hurt_103 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var xframe:String;

        public function fox_hurt_103()
        {
            addFrameScript(0, this.frame1, 8, this.frame9, 9, this.frame10, 10, this.frame11, 18, this.frame19, 19, this.frame20, 20, this.frame21, 28, this.frame29, 29, this.frame30, 30, this.frame31, 38, this.frame39, 39, this.frame40, 40, this.frame41, 48, this.frame49, 49, this.frame50, 50, this.frame51, 59, this.frame60, 68, this.frame69, 69, this.frame70, 70, this.frame71, 76, this.frame77, 78, this.frame79, 79, this.frame80, 80, this.frame81, 88, this.frame89, 89, this.frame90);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.xframe = "hurt1";
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame9():*
        {
            this.xframe = "done1";
            stop();
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("done1");
        }

        internal function frame11():*
        {
            this.xframe = "hurt2";
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame19():*
        {
            this.xframe = "done2";
            stop();
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("done2");
        }

        internal function frame21():*
        {
            this.xframe = "hurt3";
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame29():*
        {
            this.xframe = "done3";
            stop();
        }

        internal function frame30():*
        {
            this.self.stancePlayFrame("done3");
        }

        internal function frame31():*
        {
            this.xframe = "hurt4";
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame39():*
        {
            this.xframe = "done4";
            stop();
        }

        internal function frame40():*
        {
            this.self.stancePlayFrame("done4");
        }

        internal function frame41():*
        {
            this.xframe = "downed";
        }

        internal function frame49():*
        {
            this.xframe = "downed";
            stop();
        }

        internal function frame50():*
        {
            this.self.stancePlayFrame("downed");
        }

        internal function frame51():*
        {
            this.xframe = "shock";
            stop();
        }

        internal function frame60():*
        {
            this.self.stancePlayFrame("shock");
        }

        internal function frame69():*
        {
            this.xframe = "ball";
            stop();
        }

        internal function frame70():*
        {
            this.self.stancePlayFrame("ball");
        }

        internal function frame71():*
        {
            this.xframe = "faint";
        }

        internal function frame77():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("fox_landLight");
            };
        }

        internal function frame79():*
        {
            this.xframe = "faintDone";
            stop();
        }

        internal function frame80():*
        {
            this.self.stancePlayFrame("faintDone");
        }

        internal function frame81():*
        {
            this.xframe = "spin";
        }

        internal function frame89():*
        {
            this.xframe = "spin";
            stop();
        }

        internal function frame90():*
        {
            this.self.stancePlayFrame("spin");
        }


    }
}//package fox_fla

