package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_11 extends MovieClip
    {

        public var i:int;
        public var winners:Array;
        public var losers:Array;
        public var firstSimon:Boolean;
        public var hasSimon:Boolean;
        public var totalSimons:int;

        public function Win_11()
        {
            super();
            addFrameScript(0, this.frame1, 29, this.frame30, 30, this.frame31, 41, this.frame42, 89, this.frame90);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.winners = SSF2API.getWinners();
                this.losers = SSF2API.getLosers();
                this.firstSimon = false;
                this.hasSimon = false;
                this.totalSimons = 0;
                this.i = 0;
                while (this.i < this.losers.length)
                {
                    if (this.losers[this.i].getCharacterStat("statsName") === "simon")
                    {
                        this.hasSimon = true;
                        break;
                    }
                    else
                    {
                        this.i++;
                    };
                };
                this.i = 0;
                while (this.i < this.winners.length)
                {
                    if (this.winners[this.i].getCharacterStat("statsName") === "simon")
                    {
                        this.totalSimons++;
                        if ((this.winners[this.i].getID() === SSF2API.getPlayer(this).getID()) && (this.totalSimons === 1))
                        {
                            this.firstSimon = true;
                        };
                    };
                    this.i++;
                };
            };
        }

        internal function frame30():*
        {
            gotoAndPlay("Win1");
        }

        internal function frame31():*
        {
            if (this.firstSimon && this.hasSimon && (this.totalSimons === 1))
            {
                SSF2API.playSound("ssf2_snd_vfx_simon_win01_special", true);
            };
            if (!(this.firstSimon) || !(this.hasSimon))
            {
                SSF2API.playSound("ssf2_snd_vfx_simon_win01", true);
            };
        }

        internal function frame42():*
        {
            SSF2API.playSound("ssf2_snd_sfx_simon_attack_swing_m");
        }

        internal function frame90():*
        {
            gotoAndStop("loop");
        }


    }
}

