// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_specialN_air_49

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

    public dynamic class fox_specialN_air_49 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var end:*;
        public var canContinue:*;
        public var buttonReleased:Boolean;
        public var readyNext:Boolean;
        public var controls:Object;

        public function fox_specialN_air_49()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 10, this.frame11, 12, this.frame13, 14, this.frame15);
        }

        public function updateControls():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.buttonReleased = true;
            };
            if (((this.buttonReleased) && (this.controls.BUTTON1)))
            {
                this.readyNext = true;
            };
        }

        public function continueCombo():void
        {
            this.updateControls();
            if (this.end)
            {
                this.self.destroyTimer(this.continueCombo);
            }
            else
            {
                if (((this.canContinue) && (this.readyNext)))
                {
                    this.readyNext = false;
                    this.buttonReleased = false;
                    this.canContinue = false;
                    this.self.stancePlayFrame("loop");
                };
            };
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return (_arg_1);
            };
            return (_arg_1 * -1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.end = false;
            this.canContinue = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.buttonReleased = false;
                this.readyNext = false;
                this.controls = this.self.getControls();
                this.self.createTimer(1, -1, this.continueCombo);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            };
            if (((((parent) && (SSF2API.isReady())) && (this.self)) && (this.self.isCPU())))
            {
                if (((((this.self.getCPUAction() < 10) && (this.self.getCPUAction() > 0)) && (this.self.getCPULevel() >= 7)) && (this.self.isOnGround())))
                {
                    this.self.importCPUControls([128, 1, 0, 2, 64, 1, 0, 5, 0x0400, 1, 64, 1, 0, 1]);
                    this.self.setAttackEnabled(false, "b", 10);
                    this.self.endAttack();
                };
            };
        }

        internal function frame5():*
        {
            this.self.attachEffect("fox_blasterEffect");
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-26
            });
            this.self.fireProjectile("laser", 30, -12);
            this.self.playAttackSound(1);
        }

        internal function frame8():*
        {
            this.canContinue = true;
        }

        internal function frame11():*
        {
            this.canContinue = false;
            this.end = true;
            this.self.playAttackSound(2);
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }

        internal function frame15():*
        {
            this.self.playAttackSound(2);
            this.self.endAttack();
        }


    }
}//package fox_fla

