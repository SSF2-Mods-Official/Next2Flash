package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemThrow_97 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function ItemThrow_97()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 11, this.frame12, 13, this.frame14, 16, this.frame17, 23, this.frame24, 25, this.frame26, 28, this.frame29, 35, this.frame36, 37, this.frame38, 40, this.frame41, 47, this.frame48);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame5():*
        {
            this.self.tossItem(158);
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame17():*
        {
            this.self.tossItem(270);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame26():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame29():*
        {
            this.self.tossItem(90);
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame41():*
        {
            this.self.tossItem(12);
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }


    }
}

