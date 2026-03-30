package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class FTilt_30 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var opponent:*;
        public var selfFacing:Boolean;
        public var opponentFacing:Boolean;

        public function FTilt_30()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 6, this.frame7, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.opponent = null;
            this.selfFacing = false;
            this.opponentFacing = false;
        }

        internal function frame2():*
        {
        }

        internal function frame6():*
        {
            this.self.playSound("gw_ftilt01");
            this.self.attachEffect("global_dust_light");
        }

        internal function frame7():*
        {
            this.self.playSound("gw_ftilt02");
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

