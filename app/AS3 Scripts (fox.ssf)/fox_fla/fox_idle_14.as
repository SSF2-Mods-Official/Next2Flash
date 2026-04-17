// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_idle_14

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

    public dynamic class fox_idle_14 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_idle_14()
        {
            addFrameScript(0, this.frame1, 29, this.frame30, 33, this.frame34);
        }

        public function uncrouch(_arg_1:*=null):*
        {
            if (((_arg_1.data.fromState == 12) && (this.self.getGlobalVariable("crouchdown"))))
            {
                this.self.setGlobalVariable("crouchdown", false);
                this.self.stancePlayFrame("uncrouch");
            }
            else
            {
                this.self.setGlobalVariable("crouchdown", false);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (((this.self) && (SSF2API.isReady())))
            {
                if (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch))
                {
                    this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
                };
            };
        }

        internal function frame30():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame34():*
        {
            gotoAndStop("loop");
        }


    }
}//package fox_fla

