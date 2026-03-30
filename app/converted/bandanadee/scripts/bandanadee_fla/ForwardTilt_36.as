package bandanadee_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class ForwardTilt_36 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var playsound:Number;
        public var audio:Number;
        public var controls:*;

        public function ForwardTilt_36()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 5, this.frame6, 6, this.frame7, 7, this.frame8, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 25, this.frame26, 32, this.frame33);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.playSound("bandanadee_uspecSpin");
            };
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame6():*
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
            this.controls = this.self.getControls();
            if (this.controls.UP)
            {
                this.self.updateAttackBoxStats(1, {"direction":45});
                this.self.stancePlayFrame("up");
            }
            else if (this.controls.DOWN)
            {
                this.self.updateAttackBoxStats(1, {"direction":30});
                this.self.stancePlayFrame("down");
            };
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
        }

        internal function frame7():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(4), 0);
            };
        }

        internal function frame8():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(2)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(2)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(2), 0);
            };
        }

        internal function frame12():*
        {
            this.self.stancePlayFrame("end");
        }

        internal function frame13():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
        }

        internal function frame14():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(4), 0);
            };
        }

        internal function frame15():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(2)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(2)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(2), 0);
            };
        }

        internal function frame19():*
        {
            this.self.stancePlayFrame("end");
        }

        internal function frame20():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
        }

        internal function frame21():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(4), 0);
            };
        }

        internal function frame22():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(2)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(2)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(2), 0);
            };
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("end");
        }

        internal function frame33():*
        {
            this.self.endAttack();
        }


    }
}

