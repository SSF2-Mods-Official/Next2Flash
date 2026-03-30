package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class JabCombo_27 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var controls:Object;
        public var used:Boolean;
        public var time:Number;
        public var pressed1:Boolean;
        public var pressed2:Boolean;
        public var newStats:Object;

        public function JabCombo_27()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 8, this.frame9, 9, this.frame10, 11, this.frame12, 19, this.frame20, 20, this.frame21);
        }

        public function updateControls():*
        {
            this.controls = this.self.getControls();
        }

        public function continueCombo():*
        {
            if (this.used && (this.time <= 12))
            {
                this.self.stancePlayFrame("hit2");
            };
        }

        public function checkControls():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON2)
            {
                this.pressed1 = true;
            };
            if (this.pressed1 && this.controls.BUTTON2)
            {
                this.pressed2 = true;
            };
        }

        public function checkForGoToJab2():*
        {
            if (this.pressed2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("hit2");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady())
            {
                this.controls = this.self.getControls();
                this.used = this.self.getGlobalVariable("jab");
                this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
                this.self.createTimer(1, 39, this.updateControls, false);
                this.continueCombo();
            };
            this.pressed1 = false;
            this.pressed2 = false;
        }

        internal function frame3():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(38),
                "y":-16,
                "parentLock":true
            });
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("jab", true);
            this.self.createTimer(1, -1, this.checkControls, false);
            this.self.createTimer(1, -1, this.checkForGoToJab2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame9():*
        {
            this.self.endAttack();
        }

        internal function frame10():*
        {
            this.newStats = {
                "direction":35,
                "power":35,
                "kbConstant":80,
                "damage":5,
                "effectSound":"brawl_kick_m"
            };
            this.self.updateAttackBoxStats(1, this.newStats);
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
        }

        internal function frame12():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_light");
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(40),
                "y":-18,
                "parentLock":true
            });
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

