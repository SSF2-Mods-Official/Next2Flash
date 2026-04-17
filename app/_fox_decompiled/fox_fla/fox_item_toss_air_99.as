package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_item_toss_air_99 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_item_toss_air_99()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 12, this.frame13, 14, this.frame15, 16, this.frame17, 25, this.frame26, 27, this.frame28, 29, this.frame30, 38, this.frame39, 40, this.frame41, 42, this.frame43, 51, this.frame52);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame6():*
        {
            this.self.tossItem(158);
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }

        internal function frame15():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame17():*
        {
            this.self.tossItem(270);
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame30():*
        {
            this.self.tossItem(90);
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }

        internal function frame41():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame43():*
        {
            this.self.tossItem(12);
        }

        internal function frame52():*
        {
            this.self.endAttack();
        }


    }
}

