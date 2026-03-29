package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemThrowsAir_84 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function ItemThrowsAir_84()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 10, this.frame11, 12, this.frame13, 14, this.frame15, 22, this.frame23, 24, this.frame25, 26, this.frame27, 34, this.frame35, 36, this.frame37, 38, this.frame39, 46, this.frame47);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame4():*
        {
            this.self.tossItem(158);
        }

        internal function frame11():*
        {
            this.self.endAttack();
        }

        internal function frame13():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame15():*
        {
            this.self.tossItem(270);
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }

        internal function frame25():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame27():*
        {
            this.self.tossItem(90);
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }

        internal function frame37():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame39():*
        {
            this.self.tossItem(12);
        }

        internal function frame47():*
        {
            this.self.endAttack();
        }


    }
}

