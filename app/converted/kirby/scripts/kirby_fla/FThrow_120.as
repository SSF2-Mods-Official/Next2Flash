package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class FThrow_120 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;
        public var prevYLoc:Number;
        public var countDown:Number;
        public var enemy:Object;
        public var playsound:Number;
        public var audio:Number;

        public function FThrow_120()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 6, this.frame7, 7, this.frame8, 12, this.frame13, 14, this.frame15, 16, this.frame17, 19, this.frame20, 21, this.frame22, 22, this.frame23, 23, this.frame24, 24, this.frame25, 30, this.frame31);
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
                this.enemy = this.self.getGrabbedOpponents()[0];
                this.self.swapDepths(this.enemy);
            };
        }

        internal function frame3():*
        {
            this.self.swapDepths(this.enemy);
        }

        internal function frame7():*
        {
            this.self.unnattachFromGround();
            this.self.playAttackSound(1);
            this.self.setYSpeed(-12);
            this.prevYLoc = this.self.getY();
        }

        internal function frame8():*
        {
            this.self.setYSpeed(-10);
            this.self.setXSpeed(4, false);
            this.prevYLoc = this.self.getY();
        }

        internal function frame13():*
        {
            this.self.setYSpeed(0);
            this.self.playAttackSound(1);
            this.self.updateAttackStats({"air_ease":0});
            this.self.swapDepths(this.enemy);
        }

        internal function frame15():*
        {
            this.self.swapDepths(this.enemy);
        }

        internal function frame17():*
        {
            this.self.swapDepths(this.enemy);
        }

        internal function frame20():*
        {
            if ((this.self.getY() > (SSF2API.getStage().getCameraBounds().y - 100)) && !(this.countDown <= 0))
            {
                this.self.setYSpeed(-25);
                if (Math.abs((this.self.getY() - this.prevYLoc)) < 20)
                {
                    this.countDown--;
                };
                this.prevYLoc = this.self.getY();
                gotoAndStop("loop2");
            }
            else
            {
                this.self.setYSpeed(0);
            };
        }

        internal function frame22():*
        {
            this.self.setYSpeed(20);
            this.self.setXSpeed(0, false);
            this.self.updateAttackStats({"air_ease":30});
        }

        internal function frame23():*
        {
            if (!this.self.isOnGround())
            {
                gotoAndStop("loop2");
            }
            else
            {
                this.self.setYSpeed(0);
                SSF2API.getCamera().shake(10);
            };
        }

        internal function frame24():*
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
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame25():*
        {
            this.self.unnattachFromGround();
            this.self.setXSpeed(-3, false);
            this.self.setYSpeed(-10);
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

