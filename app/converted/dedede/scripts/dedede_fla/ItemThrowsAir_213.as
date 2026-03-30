package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemThrowsAir_213 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function ItemThrowsAir_213()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 11, this.frame12, 13, this.frame14, 15, this.frame16, 23, this.frame24, 25, this.frame26, 27, this.frame28, 35, this.frame36, 37, this.frame38, 39, this.frame40, 47, this.frame48);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame4():*
        {
            this.self.tossItem(270);
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame16():*
        {
            this.self.tossItem(90);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame26():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame28():*
        {
            this.self.tossItem(12);
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame40():*
        {
            this.self.tossItem(168);
        }

        internal function frame48():*
        {
            this.self.flip();
            this.self.endAttack();
        }


    }
}

