package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_30 extends MovieClip
    {

        public var stance:MovieClip;

        public function Entrance_30()
        {
            super();
            addFrameScript(6, this.frame7, 11, this.frame12, 21, this.frame22, 29, this.frame30, 39, this.frame40);
        }

        internal function frame7():*
        {
            SSF2API.playSound("entranceOpen");
        }

        internal function frame12():*
        {
            SSF2API.playSound("falcon_jumpS1");
        }

        internal function frame22():*
        {
            SSF2API.playSound("entranceClose");
        }

        internal function frame30():*
        {
            SSF2API.playSound("entranceLeave");
        }

        internal function frame40():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}

