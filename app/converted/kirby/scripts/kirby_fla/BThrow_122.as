package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class BThrow_122 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;
        public var prevYLoc:Number;
        public var countDown:Number;
        public var playsound:Number;
        public var audio:Number;

        public function BThrow_122()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 5, this.frame6, 7, this.frame8, 10, this.frame11, 11, this.frame12, 13, this.frame14, 15, this.frame16, 19, this.frame20, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = null;
            this.prevYLoc = 0;
            this.countDown = 7;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame5():*
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
            this.self.playAttackSound(1);
            this.self.unnattachFromGround();
            this.self.setYSpeed(-10);
            this.prevYLoc = this.self.getY();
        }

        internal function frame6():*
        {
            this.self.setYSpeed(-10);
            this.self.setXSpeed(-3, false);
            this.prevYLoc = this.self.getY();
        }

        internal function frame8():*
        {
            this.self.setYSpeed(0);
            this.self.updateAttackStats({"air_ease":0});
        }

        internal function frame11():*
        {
            if ((this.self.getY() > (SSF2API.getCamBounds().y - 100)) && !(this.countDown <= 0))
            {
                this.self.setYSpeed(-25);
                if (Math.abs((this.self.getY() - this.prevYLoc)) < 20)
                {
                    this.countDown--;
                };
                this.prevYLoc = this.self.getMC().y;
                gotoAndStop("loop2");
            }
            else
            {
                this.self.setYSpeed(0);
            };
        }

        internal function frame12():*
        {
            this.self.setYSpeed(20);
            this.self.setXSpeed(0, false);
            this.self.updateAttackStats({"air_ease":30});
        }

        internal function frame14():*
        {
            if (!this.self.isOnGround())
            {
                gotoAndStop("loop2");
            }
            else
            {
                SSF2API.shakeCamera(10);
                this.self.attachEffect("global_dust_cloud");
            };
        }

        internal function frame16():*
        {
            this.self.unnattachFromGround();
            this.self.setXSpeed(3, false);
            this.self.setYSpeed(-6);
        }

        internal function frame20():*
        {
            this.self.setYSpeed(5);
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

