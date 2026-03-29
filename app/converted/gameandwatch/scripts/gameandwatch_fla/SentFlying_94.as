package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class SentFlying_94 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function SentFlying_94()
        {
            super();
            addFrameScript(0, this.frame1, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            };
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

