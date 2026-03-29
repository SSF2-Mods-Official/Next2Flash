package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_85 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Crouch_85()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 34, this.frame35);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.playSound("beep_crouch_1");
            };
        }

        internal function frame3():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame35():*
        {
            this.self.stancePlayFrame("redo");
        }


    }
}

