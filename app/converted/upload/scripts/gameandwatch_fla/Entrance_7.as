package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_7 extends MovieClip
    {

        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Entrance_7()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 11, this.frame12, 22, this.frame23, 33, this.frame34, 45, this.frame46);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame2():*
        {
            if (SSF2API.isReady())
            {
                this.self.playSound("gw_entrance1");
            };
        }

        internal function frame12():*
        {
            this.self.playSound("gw_entrance2");
        }

        internal function frame23():*
        {
            this.self.playSound("gw_entrance3");
        }

        internal function frame34():*
        {
            this.self.playSound("gw_entrance4");
        }

        internal function frame46():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}

