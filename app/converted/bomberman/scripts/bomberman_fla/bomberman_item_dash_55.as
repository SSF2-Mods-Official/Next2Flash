package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_item_dash_55 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_item_dash_55()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 7, this.frame8, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame6():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame8():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

