package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_item_toss_air_108 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_item_toss_air_108()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 11, this.frame12, 12, this.frame13, 13, this.frame14, 15, this.frame16, 23, this.frame24, 24, this.frame25, 25, this.frame26, 27, this.frame28, 35, this.frame36, 36, this.frame37, 37, this.frame38, 39, this.frame40, 47, this.frame48);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame4():*
        {
            this.self.tossItem(158);
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }

        internal function frame13():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame16():*
        {
            this.self.tossItem(270);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame25():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }

        internal function frame26():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame28():*
        {
            this.self.tossItem(90);
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }

        internal function frame37():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }

        internal function frame38():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame40():*
        {
            this.self.tossItem(12);
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }


    }
}

