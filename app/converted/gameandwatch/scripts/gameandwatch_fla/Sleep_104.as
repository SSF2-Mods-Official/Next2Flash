package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Sleep_104 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Sleep_104()
        {
            super();
            addFrameScript(0, this.frame1, 94, this.frame95);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playSound("fall_asleep");
            };
        }

        internal function frame95():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

