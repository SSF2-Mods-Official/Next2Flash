package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class FThrow_63 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var touchBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;
        public var prevYLoc:Number;
        public var countDown:Number;

        public function FThrow_63()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 7, this.frame8, 13, this.frame14, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.xframe = null;
            this.prevYLoc = 0;
            this.countDown = 7;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playVoiceSound(1);
                this.self.playAttackSound(1);
            };
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame7():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-12);
            this.prevYLoc = this.self.getY();
            this.self.playSound("throw_woosh");
        }

        internal function frame8():*
        {
            this.self.setYSpeed(-10);
            this.self.setXSpeed(4, false);
            this.prevYLoc = this.self.getY();
        }

        internal function frame14():*
        {
            this.self.setYSpeed(0);
            this.self.updateAttackStats({"air_ease":0});
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
                this.self.stancePlayFrame("loop2");
            }
            else
            {
                this.self.setYSpeed(0);
            };
        }

        internal function frame21():*
        {
            this.self.setYSpeed(20);
            this.self.setXSpeed(0, false);
            this.self.updateAttackStats({"air_ease":30});
        }

        internal function frame22():*
        {
            if (!this.self.isOnGround())
            {
                this.self.stancePlayFrame("loop2");
            }
            else
            {
                this.self.setYSpeed(0);
                SSF2API.getCamera().shake(10);
            };
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame24():*
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

