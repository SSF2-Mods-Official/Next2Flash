package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class BThrow_65 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;
        public var prevYLoc:Number;
        public var countDown:Number;

        public function BThrow_65()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 10, this.frame11, 12, this.frame13, 14, this.frame15, 24, this.frame25, 29, this.frame30);
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

        internal function frame4():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-10);
            this.prevYLoc = this.self.getY();
        }

        internal function frame5():*
        {
            this.self.setYSpeed(-10);
            this.self.setXSpeed(-3, false);
            this.prevYLoc = this.self.getY();
        }

        internal function frame11():*
        {
            this.self.swapDepthsWithGrabbedOpponent(true);
        }

        internal function frame13():*
        {
            this.self.setYSpeed(0);
            this.self.updateAttackStats({"air_ease":0});
            this.self.playSound("throw_woosh");
        }

        internal function frame15():*
        {
            this.self.setYSpeed(0);
            this.self.setXSpeed(0);
        }

        internal function frame25():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }


    }
}

