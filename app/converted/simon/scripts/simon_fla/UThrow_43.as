package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class UThrow_43 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var touchBox:MovieClip;
        public var self:SimonExt;
        public var playsound:Number;
        public var audio:Number;
        public var enemy:Object;

        public function UThrow_43()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 4, this.frame5, 9, this.frame10, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
                this.self.forceGrabbedHurtFrame("spin");
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
            if (parent && this.self && SSF2API.isReady())
            {
                this.enemy = this.self.getGrabbedOpponent();
                if (!this.self.isFacingRight())
                {
                    this.enemy.setRotation(-90);
                }
                else
                {
                    this.enemy.setRotation(90);
                };
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame3():*
        {
            if (!this.self.isFacingRight())
            {
                this.enemy.setRotation(0);
            }
            else
            {
                this.enemy.setRotation(0);
            };
        }

        internal function frame5():*
        {
            if (!this.self.isFacingRight())
            {
                this.enemy.setRotation(90);
            }
            else
            {
                this.enemy.setRotation(-90);
            };
        }

        internal function frame10():*
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
            this.self.forceGrabbedHurtFrame("hurt1");
            SSF2API.getCamera().shake(10);
            this.self.attachEffect("global_dust_cloud");
            this.enemy.resetRotation();
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

