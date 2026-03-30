package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class UThrow_119 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;
        public var prevYLoc:Number;
        public var countDown:Number;
        public var grabbed:*;
        public var playsound:Number;
        public var audio:Number;

        public function UThrow_119()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12);
        }

        public function attachCamera(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.attachCamera);
            SSF2API.getCamera().addTarget(this.self.getMC());
            if (this.grabbed)
            {
                SSF2API.getCamera().addTarget(this.grabbed.getMC());
            };
        }

        public function toLand(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
            this.self.stancePlayFrame("landed");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = null;
            this.prevYLoc = 0;
            this.countDown = 4;
            this.grabbed = null;
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setXSpeed(0);
            };
        }

        internal function frame3():*
        {
            this.self.fireProjectile("throw_cam");
            this.self.unnattachFromGround();
            this.self.setYSpeed(-70);
            this.prevYLoc = this.self.getY();
            this.self.attachEffect("global_sparkle");
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
            this.grabbed = this.self.getGrabbedOpponent();
            SSF2API.getCamera().deleteTarget(this.self.getMC());
            if (this.grabbed)
            {
                SSF2API.getCamera().deleteTarget(this.grabbed.getMC());
            };
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.attachCamera, {"persistent":true});
        }

        internal function frame4():*
        {
            this.self.setYSpeed(-70);
            this.prevYLoc = this.self.getY();
            this.self.attachEffect("global_sparkle");
        }

        internal function frame5():*
        {
            if ((this.self.getY() > (SSF2API.getCamBounds().y - 100)) && !(this.countDown <= 0))
            {
                this.self.setYSpeed(-50);
                if (Math.abs((this.self.getY() - this.prevYLoc)) < 20)
                {
                    this.countDown--;
                };
                this.prevYLoc = this.self.getY();
                this.self.attachEffect("global_sparkle");
                gotoAndStop("loop");
            };
        }

        internal function frame6():*
        {
            this.self.setYSpeed((this.self.getYSpeed() * 0.75));
        }

        internal function frame8():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
        }

        internal function frame9():*
        {
            this.self.setYSpeed(70);
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop2");
        }

        internal function frame11():*
        {
            SSF2API.getCamera().shake(15);
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("effect_explosion", {
                "scaleX":2,
                "scaleY":2
            });
            this.self.unnattachFromGround();
            this.self.setXSpeed(-3, false);
            this.self.setYSpeed(-7);
            this.self.updateAttackStats({"allowControl":true});
            this.self.updateAttackBoxStats(1, {
                "burn":true,
                "effect_id":"effect_firehit_heavy"
            });
            SSF2API.getCamera().addTarget(this.self.getMC());
            if (this.grabbed)
            {
                SSF2API.getCamera().addTarget(this.grabbed.getMC());
            };
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.attachCamera);
        }

        internal function frame12():*
        {
            this.self.toJump();
            this.self.stancePlayFrame("backflip");
            this.self.setYSpeed(-(this.self.getCharacterStat("shortHopSpeed")));
            if (this.self.isFacingRight())
            {
                this.self.setXSpeed(-5);
            }
            else
            {
                this.self.setXSpeed(5);
            };
        }


    }
}

