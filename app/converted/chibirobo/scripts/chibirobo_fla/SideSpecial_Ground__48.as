package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class SideSpecial_Ground__48 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var controls:*;
        public var loop:*;
        public var hasBoosted:*;
        public var sfxStop:*;

        public function SideSpecial_Ground__48()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 7, this.frame8, 12, this.frame13, 18, this.frame19, 19, this.frame20, 30, this.frame31, 35, this.frame36);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function buttonCheck():void
        {
            this.self.setXSpeed(15, false);
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.stancePlayFrame("endlag");
            };
            this.self.refreshAttackID();
        }

        public function pullBack():void
        {
            if (this.hasBoosted)
            {
                if (this.self.isOnGround())
                {
                    this.self.setXSpeed(-5, false);
                }
                else
                {
                    this.self.setXSpeed(-1, false);
                };
            };
        }

        public function bubbles():void
        {
            this.self.attachEffectOverlay("soapBubbles");
        }

        public function clean():void
        {
            if (this.self.isOnGround())
            {
                this.self.attachEffectOverlay("floorTwinkle");
            };
        }

        public function clearSound(_arg_1:*=null):*
        {
            SSF2API.stopSound(this.sfxStop);
        }

        public function slowDown():void
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.85));
            if ((this.self.isFacingRight() && (this.self.getXSpeed() < 1)) || (!(this.self.isFacingRight()) && (this.self.getXSpeed() > -1)))
            {
                this.self.setXSpeed(0);
                this.self.destroyTimer(this.slowDown);
                SSF2API.stopSound(this.sfxStop);
                this.self.destroyTimer(this.bubbles);
                this.self.destroyTimer(this.clean);
                this.self.stancePlayFrame("end");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.controls = null;
            this.loop = 0;
            this.hasBoosted = false;
            this.sfxStop = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("global_sparkle", {
                    "x":this.flipX(-20),
                    "y":-55
                });
            };
        }

        internal function frame6():*
        {
        }

        internal function frame7():*
        {
            if (this.loop == 0)
            {
                if (!this.self.getMetalStatus())
                {
                    this.sfxStop = this.self.playAttackSound(1);
                };
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.clearSound);
                this.self.createTimer(6, -1, this.pullBack);
                this.self.createTimer(12, -1, this.buttonCheck);
                this.self.createTimer(4, -1, this.bubbles);
                this.self.createTimer(12, -1, this.clean);
            };
        }

        internal function frame8():*
        {
            this.hasBoosted = true;
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame19():*
        {
            this.loop++;
            this.self.stancePlayFrame("loop");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame20():*
        {
            this.self.destroyTimer(this.buttonCheck);
            this.self.destroyTimer(this.pullBack);
            this.self.createTimer(1, -1, this.slowDown);
        }

        internal function frame31():*
        {
            this.self.stancePlayFrame("endloop");
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }


    }
}

