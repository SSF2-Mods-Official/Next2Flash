package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class UpThrow_189 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var touchBox:MovieClip;
        public var self:DededeExt;
        public var playsound:Number;
        public var audio:Number;
        public var target:*;
        public var grab:*;

        public function UpThrow_189()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 11, this.frame12, 14, this.frame15, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame11():*
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
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame12():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame15():*
        {
            this.self.attachEffect("global_dust_cloud");
            SSF2API.getCamera().shake(7);
        }

        internal function frame25():*
        {
            this.target = null;
            this.grab = 0;
            if (this.self.isCPU())
            {
                this.target = this.self.getGrabbedOpponents()[0];
                this.grab = SSF2API.random();
                if ((this.target != null) && (this.target.getDamage() >= 70))
                {
                    if (this.grab <= 0.8)
                    {
                        this.self.importCPUControls([128, 7, 2208, 1]);
                    };
                }
                else if (this.target != null)
                {
                    if ((this.grab <= 0.4) && (this.target.getDamage() <= 50))
                    {
                        this.self.importCPUControls([6305, 1]);
                    }
                    else if (this.grab <= 0.5)
                    {
                        this.self.importCPUControls([128, 7, 4129, 1]);
                    }
                    else if (this.grab <= 0.75)
                    {
                        this.self.importCPUControls([128, 7, 4385, 1]);
                    }
                    else
                    {
                        this.self.importCPUControls([128, 7, 4641, 1]);
                    };
                };
            };
            this.self.endAttack();
        }


    }
}

