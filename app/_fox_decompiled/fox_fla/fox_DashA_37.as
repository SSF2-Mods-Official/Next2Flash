package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_DashA_37 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var playsound:Number;
        public var audio:Number;
        public var canCancel:Boolean;
        public var controls:*;

        public function fox_DashA_37()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 13, this.frame14, 15, this.frame16, 16, this.frame17, 20, this.frame21);
        }

        public function moveForward():void
        {
            this.self.setXSpeed(8, false);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (parent && SSF2API.isReady() && this.self)
                {
                    this.playsound = SSF2API.random();
                    this.audio = this.self.getGlobalVariable("audio");
                };
            };
            if (parent && SSF2API.isReady() && this.self)
            {
                this.canCancel = true;
                this.controls = this.self.getControls();
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, 7, this.moveForward);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame3():*
        {
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            if (this.self && SSF2API.isReady())
            {
                this.self.attachEffect("global_dust_blast", {
                    "x":this.self.flipX(50),
                    "y":-20,
                    "parentLock":true
                });
                this.self.playAttackSound(1);
            };
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("fox_footstep");
            };
            this.self.updateAttackStats({"xSpeedDecay":1});
        }

        internal function frame16():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("fox_footstep2");
            };
        }

        internal function frame17():*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.5));
        }

        internal function frame21():*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.5));
            this.self.endAttack();
        }


    }
}

