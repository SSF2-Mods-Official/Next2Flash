// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Idle_3

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
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

    public dynamic class Idle_3 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var used:Boolean;
        public var rand:int;
        public var repeats:int;

        public function Idle_3()
        {
            addFrameScript(0, this.frame1, 11, this.frame12, 35, this.frame36, 65, this.frame66, 69, this.frame70);
        }

        public function restoreSpecials():*
        {
            this.self.setAttackEnabled(true, "b_forward");
            this.self.setAttackEnabled(true, "b_forward_air");
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
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.used = false;
            this.rand = 0;
            if (!this.repeats)
            {
                this.repeats = 0;
            };
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.rand = (100 * SSF2API.random());
                if (this.rand >= 95)
                {
                    this.gotoAndStop("bored");
                }
                else
                {
                    if (this.rand >= 85)
                    {
                        this.gotoAndStop("blink");
                    };
                };
            };
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.restoreSpecials();
            };
            if (((this.self) && (SSF2API.isReady())))
            {
                if (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch))
                {
                    this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
                };
            };
        }

        internal function frame12():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame36():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame66():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame70():*
        {
            gotoAndStop("loop");
        }


    }
}//package blackmage_fla

