package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_ledge_roll_84 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_ledge_roll_84()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("bomberman_jump1");
        }

        internal function frame7():*
        {
            this.self.playSound("bomberman_dash");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame25():*
        {
            this.self.playSound("bomberman_step2");
            this.self.endAttack();
        }


    }
}

