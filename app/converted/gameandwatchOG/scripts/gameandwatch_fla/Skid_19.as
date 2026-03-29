package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_19 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Skid_19()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady())
            {
                this.self.playSound("gw_dash_stop");
            };
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }


    }
}

